'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  Wand2,
  Library,
  Calendar,
  Send,
  Settings,
  BarChart2,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/create', label: 'İçerik Oluştur', icon: Wand2 },
  { href: '/library', label: 'İçerik Kütüphanesi', icon: Library },
  { href: '/calendar', label: 'Takvim', icon: Calendar },
  { href: '/auto-publish', label: 'Otomatik Yayın', icon: Send },
  { href: '/brand-settings', label: 'Marka Ayarları', icon: Settings },
  { href: '/competitor', label: 'Rakip Analizi', icon: BarChart2 },
]

export function SidebarNav() {
  const pathname = usePathname()

  return (
    <nav className="flex-1 px-3 py-2">
      {navItems.map((item) => {
        const Icon = item.icon
        const active = pathname === item.href || pathname.startsWith(item.href + '/')
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium mb-0.5 transition-colors',
              active
                ? 'bg-blue-50 text-blue-700'
                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
            )}
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {item.label}
          </Link>
        )
      })}
    </nav>
  )
}
