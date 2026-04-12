import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Login sayfası ve statik dosyalar geç
  if (
    pathname.startsWith('/login') ||
    pathname.startsWith('/_next') ||
    pathname.startsWith('/favicon')
  ) {
    return NextResponse.next()
  }

  const authCookie = request.cookies.get('crm-auth')

  if (!authCookie?.value) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // Cookie değeri: sha256(CRM_PASSWORD + salt) — actions.ts'te set ediliyor
  // Edge runtime'da env değişkeni okunabilir, crypto.subtle ile hash doğrulama yapılır
  const password = process.env.CRM_PASSWORD
  if (!password) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  const encoder = new TextEncoder()
  const data = encoder.encode(password + 'otomaix-crm-salt-2026')
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  const expectedToken = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')

  if (authCookie.value !== expectedToken) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
