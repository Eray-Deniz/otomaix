'use client'

import { Toaster } from '@/components/ui/sonner'
import { CrispProvider } from './CrispProvider'
import { PostHogProvider } from './PostHogProvider'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <PostHogProvider>
      <CrispProvider>
        {children}
        <Toaster position="bottom-right" richColors />
      </CrispProvider>
    </PostHogProvider>
  )
}
