import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Otomaix CRM',
  description: 'Otomaix Müşteri Yönetim Paneli',
  robots: 'noindex, nofollow',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="tr">
      <body className="antialiased">{children}</body>
    </html>
  )
}
