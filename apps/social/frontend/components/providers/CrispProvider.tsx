'use client'

import { useEffect } from 'react'

// Crisp global tip tanımları
declare global {
  interface Window {
    $crisp: unknown[][]
    CRISP_WEBSITE_ID: string
  }
}

export function CrispProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const websiteId = process.env.NEXT_PUBLIC_CRISP_WEBSITE_ID
    if (!websiteId || typeof window === 'undefined') return

    // Crisp API kuyruğunu ve kimliğini ayarla
    window.$crisp = []
    window.CRISP_WEBSITE_ID = websiteId

    // Türkçe dil
    window.$crisp.push(['config', 'locale', ['tr']])
    // Otomaix marka rengi (violet-600)
    window.$crisp.push(['config', 'color:theme', ['purple']])
    // Sağ alt köşe (varsayılan, açıkça belirt)
    window.$crisp.push(['config', 'position:reverse', [false]])

    // Crisp loader script'ini yükle
    const script = document.createElement('script')
    script.src = 'https://client.crisp.chat/l.js'
    script.async = true
    document.head.appendChild(script)

    return () => {
      // Temizlik: component unmount olursa scripti kaldır
      const existing = document.querySelector('script[src="https://client.crisp.chat/l.js"]')
      if (existing) existing.remove()
    }
  }, [])

  return <>{children}</>
}

/**
 * Kullanıcı oturum açtıktan sonra Crisp'e kimlik bilgilerini gönderir.
 * dashboard/layout.tsx içinden çağrılır.
 */
export function crispIdentify(user: {
  id: string
  email: string
  name?: string | null
  plan_id?: string
  brands_count?: number
}) {
  if (typeof window === 'undefined' || !window.$crisp) return
  try {
    window.$crisp.push(['set', 'user:email', [user.email]])
    if (user.name) {
      window.$crisp.push(['set', 'user:nickname', [user.name]])
    }
    window.$crisp.push(['set', 'session:data', [[
      ['account_id', user.id],
      ['plan', user.plan_id ?? 'starter'],
      ['brands_count', String(user.brands_count ?? 0)],
    ]]])
  } catch {
    // Crisp henüz yüklenmediyse sessizce atla
  }
}

/**
 * Kullanıcı çıkış yaptığında Crisp oturumunu sıfırlar.
 */
export function crispReset() {
  if (typeof window === 'undefined' || !window.$crisp) return
  try {
    window.$crisp.push(['do', 'session:reset'])
  } catch {
    // ignore
  }
}
