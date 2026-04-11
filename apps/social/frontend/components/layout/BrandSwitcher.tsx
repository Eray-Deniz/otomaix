'use client'

import { useState } from 'react'
import { useAppStore } from '@/lib/store'
import { useRouter } from 'next/navigation'
import {
  Check,
  ChevronDown,
  Plus,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import Image from 'next/image'

export function BrandSwitcher() {
  const { currentBrand, brands, switchBrand } = useAppStore()
  const [open, setOpen] = useState(false)
  const router = useRouter()

  function handleSelect(brandId: string) {
    const brand = brands.find((b) => b.id === brandId)
    if (brand) switchBrand(brand)
    setOpen(false)
  }

  function handleAddBrand() {
    setOpen(false)
    router.push('/markalar')
  }

  const initials = (name: string) =>
    name
      .split(' ')
      .slice(0, 2)
      .map((w) => w[0])
      .join('')
      .toUpperCase()

  return (
    <div className="relative px-3 py-2 border-b border-gray-100">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center gap-2.5 px-2 py-2 rounded-lg hover:bg-gray-50 transition-colors group"
      >
        {/* Brand avatar */}
        <div className="w-7 h-7 rounded-md bg-blue-100 flex items-center justify-center shrink-0 overflow-hidden">
          {currentBrand?.logo_light_url ? (
            <Image
              src={currentBrand.logo_light_url}
              alt={currentBrand.name}
              width={28}
              height={28}
              className="object-contain"
            />
          ) : (
            <span className="text-xs font-bold text-blue-600">
              {currentBrand ? initials(currentBrand.name) : '?'}
            </span>
          )}
        </div>

        {/* Brand name */}
        <div className="flex-1 min-w-0 text-left">
          <p className="text-sm font-semibold text-gray-900 truncate">
            {currentBrand?.name || 'Marka Seç'}
          </p>
          {currentBrand?.sector && (
            <p className="text-xs text-gray-400 truncate capitalize">
              {currentBrand.sector}
            </p>
          )}
        </div>

        <ChevronDown
          className={cn(
            'w-4 h-4 text-gray-400 shrink-0 transition-transform',
            open && 'rotate-180'
          )}
        />
      </button>

      {/* Dropdown */}
      {open && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setOpen(false)}
          />

          <div className="absolute left-3 right-3 top-full mt-1 z-20 bg-white border border-gray-200 rounded-xl shadow-lg py-1 overflow-hidden">
            {brands.length === 0 ? (
              <p className="text-xs text-gray-400 px-3 py-2 text-center">
                Henüz marka yok
              </p>
            ) : (
              brands.map((brand) => (
                <button
                  key={brand.id}
                  onClick={() => handleSelect(brand.id)}
                  className="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-gray-50 transition-colors text-left"
                >
                  {/* Avatar */}
                  <div className="w-6 h-6 rounded-md bg-blue-100 flex items-center justify-center shrink-0 overflow-hidden">
                    {brand.logo_light_url ? (
                      <Image
                        src={brand.logo_light_url}
                        alt={brand.name}
                        width={24}
                        height={24}
                        className="object-contain"
                      />
                    ) : (
                      <span className="text-xs font-bold text-blue-600">
                        {initials(brand.name)}
                      </span>
                    )}
                  </div>

                  <span className="flex-1 text-sm text-gray-800 truncate">
                    {brand.name}
                  </span>

                  {currentBrand?.id === brand.id && (
                    <Check className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                  )}
                </button>
              ))
            )}

            {/* Ayırıcı */}
            <div className="border-t border-gray-100 mt-1 pt-1">
              <button
                onClick={handleAddBrand}
                className="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-gray-50 transition-colors text-left text-blue-600"
              >
                <div className="w-6 h-6 rounded-md border-2 border-dashed border-blue-300 flex items-center justify-center shrink-0">
                  <Plus className="w-3 h-3" />
                </div>
                <span className="text-sm font-medium">Yeni Marka Ekle</span>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
