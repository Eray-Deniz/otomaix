'use client'

import { useState } from 'react'
import { addCommunication } from '@/app/customer-actions'

export function AddCommunicationForm({ accountId }: { accountId: string }) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    channel: 'email',
    direction: 'outbound',
    subject: '',
    note: '',
    createdBy: 'Eray',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    await addCommunication(accountId, form)
    setForm({ channel: 'email', direction: 'outbound', subject: '', note: '', createdBy: 'Eray' })
    setOpen(false)
    setLoading(false)
  }

  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }))

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="text-xs text-green-600 hover:underline"
      >
        + İletişim Kaydı Ekle
      </button>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-2 bg-gray-50 rounded-lg p-3">
      <div className="flex gap-2">
        <select
          value={form.channel}
          onChange={set('channel')}
          className="flex-1 text-xs border border-gray-200 rounded-lg px-2 py-1.5 bg-white focus:outline-none"
        >
          <option value="email">Email</option>
          <option value="telefon">Telefon</option>
          <option value="toplanti">Toplantı</option>
          <option value="telegram">Telegram</option>
        </select>
        <select
          value={form.direction}
          onChange={set('direction')}
          className="flex-1 text-xs border border-gray-200 rounded-lg px-2 py-1.5 bg-white focus:outline-none"
        >
          <option value="outbound">Giden</option>
          <option value="inbound">Gelen</option>
        </select>
      </div>
      <input
        value={form.subject}
        onChange={set('subject')}
        placeholder="Konu (opsiyonel)"
        className="w-full text-xs border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:border-blue-400"
      />
      <textarea
        value={form.note}
        onChange={set('note')}
        placeholder="Not..."
        rows={2}
        className="w-full text-xs border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:border-blue-400 resize-none"
      />
      <div className="flex items-center gap-2">
        <input
          value={form.createdBy}
          onChange={set('createdBy')}
          placeholder="Ekleyen"
          className="flex-1 text-xs border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="text-xs bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white px-3 py-1.5 rounded-lg"
        >
          {loading ? 'Kaydediliyor...' : 'Kaydet'}
        </button>
        <button type="button" onClick={() => setOpen(false)} className="text-xs text-gray-500">
          İptal
        </button>
      </div>
    </form>
  )
}
