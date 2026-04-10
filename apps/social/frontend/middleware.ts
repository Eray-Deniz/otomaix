import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(req: NextRequest) {
  // Supabase auth token cookie kontrolü (sb-<project>-auth-token)
  const hasCookie = req.cookies.getAll().some((c) => c.name.startsWith('sb-') && c.name.endsWith('-auth-token'))

  const isAuthPage = req.nextUrl.pathname.startsWith('/login')
  const isProtected =
    req.nextUrl.pathname.startsWith('/dashboard') ||
    req.nextUrl.pathname.startsWith('/onboarding')

  if (!hasCookie && isProtected) {
    return NextResponse.redirect(new URL('/login', req.url))
  }

  if (hasCookie && isAuthPage) {
    return NextResponse.redirect(new URL('/dashboard', req.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/onboarding/:path*', '/login'],
}
