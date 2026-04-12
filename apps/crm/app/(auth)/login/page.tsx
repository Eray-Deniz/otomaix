'use client'

import { useFormState, useFormStatus } from 'react-dom'
import { login } from '@/app/actions'

function SubmitButton() {
  const { pending } = useFormStatus()
  return (
    <button
      type="submit"
      disabled={pending}
      className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium py-2.5 rounded-lg text-sm transition-colors"
    >
      {pending ? 'Giriş yapılıyor...' : 'Giriş Yap'}
    </button>
  )
}

export default function LoginPage() {
  const [state, formAction] = useFormState(login, null)

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#1a1a2e]">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-2">
            <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">O</span>
            </div>
            <span className="text-white font-bold text-xl">Otomaix</span>
          </div>
          <p className="text-[#a8b2d8] text-sm">CRM Admin Paneli</p>
        </div>

        {/* Form */}
        <div className="bg-[#16213e] rounded-xl p-6 border border-[#2a2a4a]">
          <h1 className="text-white font-semibold text-lg mb-6">Giriş Yap</h1>

          <form action={formAction} className="space-y-4">
            <div>
              <label className="block text-[#a8b2d8] text-xs font-medium mb-1.5 uppercase tracking-wider">
                Şifre
              </label>
              <input
                type="password"
                name="password"
                required
                autoFocus
                className="w-full px-3 py-2.5 bg-[#1a1a2e] border border-[#2a2a4a] rounded-lg text-white placeholder-[#4a5568] focus:outline-none focus:border-blue-500 text-sm"
                placeholder="••••••••••••"
              />
            </div>

            {state?.error && (
              <div className="bg-red-900/30 border border-red-700 text-red-300 text-sm px-3 py-2 rounded-lg">
                {state.error}
              </div>
            )}

            <SubmitButton />
          </form>
        </div>

        <p className="text-center text-[#4a5568] text-xs mt-6">
          Sadece Otomaix ekibi erişebilir
        </p>
      </div>
    </div>
  )
}
