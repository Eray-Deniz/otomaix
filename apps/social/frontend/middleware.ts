import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Auth koruması app/(dashboard)/layout.tsx içinde client-side yapılıyor.
// Supabase session localStorage'da tutulduğu için middleware'den okunamaz.
export function middleware(_req: NextRequest) {
  return NextResponse.next()
}

export const config = {
  matcher: [],
}
