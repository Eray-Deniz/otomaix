'use client'

export const dynamic = 'force-dynamic'

import { useState } from 'react'
import { createSupabaseClient } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function KayitPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const supabase = createSupabaseClient()

  async function handleGoogleSignup() {
    setLoading(true)
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: `${window.location.origin}/auth/callback` },
    })
    if (error) setError(error.message)
    setLoading(false)
  }

  async function handleEmailSignup(e: React.FormEvent) {
    e.preventDefault()
    if (!email.trim() || !password.trim()) return
    setLoading(true)
    setError('')
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { full_name: name.trim() || undefined },
        emailRedirectTo: `${window.location.origin}/auth/callback`,
      },
    })
    if (error) {
      setError(error.message)
      setLoading(false)
    } else {
      setSuccess(true)
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 w-full max-w-sm text-center">
        <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-2xl">✉️</span>
        </div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">E-postanızı Doğrulayın</h2>
        <p className="text-sm text-gray-500 mb-6 leading-relaxed">
          <strong className="text-gray-700">{email}</strong> adresine doğrulama linki gönderdik.
          Linke tıkladıktan sonra hesabınız aktifleşecek.
        </p>
        <p className="text-xs text-gray-400">
          E-posta gelmedi mi?{' '}
          <button
            onClick={() => setSuccess(false)}
            className="text-blue-600 hover:underline"
          >
            Tekrar dene
          </button>
        </p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 w-full max-w-sm">
      <div className="flex flex-col items-center mb-6">
        <span className="text-2xl font-bold text-gray-900 tracking-tight">Otomaix</span>
        <span className="text-xs text-gray-400 font-medium mt-0.5">14 gün ücretsiz dene</span>
      </div>

      <h1 className="text-xl font-semibold text-gray-900 mb-1">Hesap Oluşturun</h1>
      <p className="text-sm text-gray-500 mb-6">Kredi kartı gerekmez</p>

      <Button
        onClick={handleGoogleSignup}
        disabled={loading}
        className="w-full mb-4 bg-white text-gray-800 border border-gray-200 hover:bg-gray-50"
        variant="outline"
      >
        <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
        </svg>
        Google ile Kayıt Ol
      </Button>

      <div className="relative mb-4">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-200" />
        </div>
        <div className="relative flex justify-center text-xs">
          <span className="bg-white px-2 text-gray-400">veya e-posta ile devam et</span>
        </div>
      </div>

      <form onSubmit={handleEmailSignup} className="space-y-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Ad Soyad</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Adınız Soyadınız"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">E-posta *</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="ornek@email.com"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Şifre *</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="En az 8 karakter"
            minLength={8}
            required
          />
        </div>
        {error && <p className="text-xs text-red-500">{error}</p>}
        <Button type="submit" disabled={loading || !email.trim() || !password.trim()} className="w-full">
          {loading ? 'Hesap oluşturuluyor...' : 'Ücretsiz Hesap Oluştur'}
        </Button>
      </form>

      <p className="text-xs text-gray-400 text-center mt-4">
        Zaten hesabınız var mı?{' '}
        <Link href="/login" className="text-blue-600 hover:underline font-medium">
          Giriş yapın
        </Link>
      </p>

      <p className="text-xs text-gray-400 text-center mt-3 leading-relaxed">
        Kayıt olarak{' '}
        <a href="mailto:destek@otomaix.com" className="underline">Kullanım Koşullarını</a>
        {' '}kabul etmiş olursunuz.
      </p>
    </div>
  )
}
