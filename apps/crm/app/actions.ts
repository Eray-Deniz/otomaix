'use server'

import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

async function computeSessionToken(password: string): Promise<string> {
  const encoder = new TextEncoder()
  const data = encoder.encode(password + 'otomaix-crm-salt-2026')
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
}

export async function login(
  _prevState: { error?: string } | null,
  formData: FormData
): Promise<{ error: string }> {
  const password = formData.get('password') as string

  if (!password) {
    return { error: 'Şifre giriniz' }
  }

  const expectedPassword = process.env.CRM_PASSWORD
  if (!expectedPassword || password !== expectedPassword) {
    return { error: 'Şifre hatalı' }
  }

  const token = await computeSessionToken(password)

  const cookieStore = await cookies()
  cookieStore.set('crm-auth', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 60 * 60 * 24 * 7, // 7 gün
    path: '/',
  })

  redirect('/')
}

export async function logout() {
  const cookieStore = await cookies()
  cookieStore.delete('crm-auth')
  redirect('/login')
}
