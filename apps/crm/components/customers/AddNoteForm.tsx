'use client'

import { useState } from 'react'
import { addNote } from '@/app/customer-actions'

export function AddNoteForm({ accountId }: { accountId: string }) {
  const [open, setOpen] = useState(false)
  const [note, setNote] = useState('')
  const [author, setAuthor] = useState('Eray')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!note.trim()) return
    setLoading(true)
    await addNote(accountId, note, author)
    setNote('')
    setOpen(false)
    setLoading(false)
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="text-xs text-blue-600 hover:underline"
      >
        + İç Not Ekle
      </button>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <textarea
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder="Not içeriği..."
        rows={3}
        className="w-full text-xs border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-400 resize-none"
      />
      <div className="flex items-center gap-2">
        <input
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
          placeholder="Ekleyen adı"
          className="flex-1 text-xs border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:border-blue-400"
        />
        <button
          type="submit"
          disabled={loading || !note.trim()}
          className="text-xs bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-3 py-1.5 rounded-lg"
        >
          {loading ? 'Kaydediliyor...' : 'Kaydet'}
        </button>
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="text-xs text-gray-500 hover:text-gray-700"
        >
          İptal
        </button>
      </div>
    </form>
  )
}
