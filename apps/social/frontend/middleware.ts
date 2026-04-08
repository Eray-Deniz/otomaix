import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { createBrowserClient } from '@supabase/auth-helpers-nextjs'

export async function middleware(req: NextRequest) {
  const res = NextResponse.next()

  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )

  const { data: { session } } = await supabase.auth.getSession()

  const isAuthPage = req.nextUrl.pathname.startsWith('/login')
  const isDashboard = req.nextUrl.pathname.startsWith('/dashboard')

  if (!session && isDashboard) {
    return NextResponse.redirect(new URL('/login', req.url))
  }

  if (session && isAuthPage) {
    return NextResponse.redirect(new URL('/dashboard', req.url))
  }

  return res
}

export const config = {
  matcher: ['/dashboard/:path*', '/login'],
}
