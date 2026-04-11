'use client'

import { Toaster } from '@/components/ui/sonner'
import { PostHogProvider } from './PostHogProvider'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <PostHogProvider>
      {children}
      <Toaster position="bottom-right" richColors />
    </PostHogProvider>
  )
}
