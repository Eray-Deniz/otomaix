'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'
import { toast } from 'sonner'
import { Loader2, MessageCircle, Save } from 'lucide-react'

interface WorkspaceSettings {
  telegram_bot_token: string
  telegram_chat_id: string
}

export default function AyarlarPage() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [botToken, setBotToken] = useState('')
  const [chatId, setChatId] = useState('')

  useEffect(() => {
    api.get<WorkspaceSettings>('/settings').then((res) => {
      if (res.success && res.data) {
        setBotToken(res.data.telegram_bot_token ?? '')
        setChatId(res.data.telegram_chat_id ?? '')
      }
      setLoading(false)
    })
  }, [])

  async function handleSave() {
    setSaving(true)
    const res = await api.patch('/settings', {
      telegram_bot_token: botToken,
      telegram_chat_id: chatId,
    })
    setSaving(false)
    if (res.success) {
      toast.success('Ayarlar kaydedildi')
    } else {
      toast.error(res.error ?? 'Kaydetme başarısız')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
      </div>
    )
  }

  return (
    <div className="p-8 max-w-xl mx-auto">
      <div className="mb-8">
        <h1 className="text-xl font-bold text-gray-900">Ayarlar</h1>
        <p className="text-sm text-gray-500 mt-0.5">Workspace geneli entegrasyon ayarları</p>
      </div>

      {/* Telegram */}
      <div className="bg-white border border-gray-100 rounded-2xl p-6 space-y-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center">
            <MessageCircle className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">Telegram Entegrasyonu</h2>
            <p className="text-xs text-gray-500 mt-0.5">
              İçerik onayı için kullanılır — tüm markalarınız bu Telegram&apos;a bildirim gönderir
            </p>
          </div>
        </div>

        {/* Setup guide */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 space-y-1.5">
          <p className="text-xs font-semibold text-blue-800">Telegram botunuzu nasıl oluşturursunuz:</p>
          <ol className="text-xs text-blue-700 space-y-1 list-decimal list-inside">
            <li>Telegram&apos;da <strong>@BotFather</strong>&apos;a yazın</li>
            <li><strong>/newbot</strong> komutunu gönderin ve bot adını belirleyin</li>
            <li>Aldığınız token&apos;ı aşağıya yapıştırın</li>
            <li>Bota bir mesaj atın, ardından <strong>@userinfobot</strong>&apos;a yazarak Chat ID&apos;nizi öğrenin</li>
          </ol>
        </div>

        <div className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-700">Bot Token</label>
            <input
              type="text"
              value={botToken}
              onChange={(e) => setBotToken(e.target.value)}
              placeholder="1234567890:AABBCCDDEEFFaabbccddeeff"
              className="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-700">Chat ID</label>
            <input
              type="text"
              value={chatId}
              onChange={(e) => setChatId(e.target.value)}
              placeholder="@userinfobot'tan aldığınız ID (örn: 1634464595)"
              className="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400"
            />
          </div>
        </div>

        <Button
          onClick={handleSave}
          disabled={saving}
          className="w-full gap-2"
        >
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          Kaydet
        </Button>
      </div>
    </div>
  )
}
