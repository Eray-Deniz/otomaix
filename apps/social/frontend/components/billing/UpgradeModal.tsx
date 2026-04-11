'use client'

import { Button } from '@/components/ui/button'
import { Zap, X } from 'lucide-react'
import Link from 'next/link'

interface UpgradeModalProps {
  message: string
  onClose: () => void
}

export function UpgradeModal({ message, onClose }: UpgradeModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm mx-4 p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center justify-center w-12 h-12 bg-blue-50 rounded-xl mb-4 mx-auto">
          <Zap className="w-6 h-6 text-blue-600" />
        </div>

        <h2 className="text-lg font-bold text-gray-900 text-center mb-2">
          Plan Yükseltme Gerekli
        </h2>

        <p className="text-sm text-gray-500 text-center mb-6">{message}</p>

        <div className="flex flex-col gap-2">
          <Link href="/fiyatlandirma" onClick={onClose}>
            <Button className="w-full gap-2">
              <Zap className="w-4 h-4" />
              Planı Yükselt
            </Button>
          </Link>
          <Button variant="ghost" className="w-full text-gray-500" onClick={onClose}>
            Şimdi Değil
          </Button>
        </div>
      </div>
    </div>
  )
}
