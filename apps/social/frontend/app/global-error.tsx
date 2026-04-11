'use client'

import * as Sentry from '@sentry/nextjs'
import { useEffect } from 'react'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    Sentry.captureException(error)
  }, [error])

  return (
    <html lang="tr">
      <body>
        <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-[#F6F7F9] text-center">
          <h1 className="text-2xl font-bold text-gray-900">Beklenmeyen bir hata oluştu</h1>
          <p className="text-gray-500">Ekibimiz bilgilendirildi. Lütfen sayfayı yenileyin.</p>
          <button
            onClick={reset}
            className="rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700"
          >
            Tekrar Dene
          </button>
        </div>
      </body>
    </html>
  )
}
