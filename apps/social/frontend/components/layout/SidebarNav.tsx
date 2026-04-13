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
  TrendingUp,
  CreditCard,
  Building2,
  SlidersHorizontal,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/icerik-olustur', label: 'İçerik Oluştur', icon: Wand2 },
  { href: '/icerik-kutuphanesi', label: 'İçerik Kütüphanesi', icon: Library },
  { href: '/takvim', label: 'Takvim', icon: Calendar },
  { href: '/otomatik-yayin', label: 'Otomatik Yayın', icon: Send },
  { href: '/marka-ayarlari', label: 'Marka Ayarları', icon: Settings },
  { href: '/rakip-analizi', label: 'Rakip Analizi', icon: BarChart2 },
  { href: '/trendler', label: 'Trendler', icon: TrendingUp },
  { href: '/markalar', label: 'Markalar', icon: Building2 },
  { href: '/faturalandirma', label: 'Faturalandırma', icon: CreditCard },
  { href: '/ayarlar', label: 'Ayarlar', icon: SlidersHorizontal },
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
