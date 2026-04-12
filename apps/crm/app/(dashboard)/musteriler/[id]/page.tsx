import { query, queryOne } from '@/lib/db'
import { notFound } from 'next/navigation'
import {
  cn,
  PLAN_COLORS,
  PLAN_LABELS,
  STATUS_COLORS,
  STATUS_LABELS,
  relativeTime,
  formatDate,
} from '@/lib/utils'
import { CustomerActions } from '@/components/customers/CustomerActions'
import { AddNoteForm } from '@/components/customers/AddNoteForm'
import { AddCommunicationForm } from '@/components/customers/AddCommunicationForm'
import { TagManager } from '@/components/customers/TagManager'
import { ArrowLeft, ExternalLink } from 'lucide-react'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

interface CustomerDetail {
  id: string
  email: string
  name: string | null
  plan_id: string
  created_at: string
  last_login_at: string | null
  trial_ends_at: string | null
  subscription_status: string
  current_period_end: string | null
  paddle_customer_id: string | null
  brand_count: string
  tags: string[] | null
  total_posts_generated: string
  total_posts_published: string
}

interface Brand {
  id: string
  name: string
  sector: string | null
  created_at: string
  post_count: string
}

interface Note {
  id: string
  note: string
  created_by: string
  created_at: string
}

interface Communication {
  id: string
  channel: string
  direction: string
  subject: string | null
  note: string | null
  created_by: string
  created_at: string
}

async function getCustomerDetail(id: string) {
  const [customer, brands, notes, communications, monthlyUsage] = await Promise.all([
    queryOne<CustomerDetail>(
      `SELECT * FROM crm.customer_overview WHERE id = $1`,
      [id]
    ),
    query<Brand>(`
      SELECT b.id, b.name, b.sector, b.created_at,
             COUNT(p.id)::text as post_count
      FROM social.brands b
      JOIN social.workspaces w ON w.id = b.workspace_id
      WHERE w.account_id = $1 AND b.is_active = true
      GROUP BY b.id, b.name, b.sector, b.created_at
      ORDER BY b.created_at DESC
    `, [id]),
    query<Note>(
      `SELECT * FROM crm.account_notes WHERE account_id = $1 ORDER BY created_at DESC`,
      [id]
    ),
    query<Communication>(
      `SELECT * FROM crm.account_communications WHERE account_id = $1 ORDER BY created_at DESC`,
      [id]
    ),
    query<{ year_month: string; posts_generated: number; posts_published: number }>(
      `SELECT year_month, SUM(posts_generated)::int as posts_generated, SUM(posts_published)::int as posts_published
       FROM crm.monthly_usage WHERE account_id = $1
       GROUP BY year_month ORDER BY year_month DESC LIMIT 3`,
      [id]
    ),
  ])

  return { customer, brands, notes, communications, monthlyUsage }
}

export default async function CustomerDetailPage({
  params,
}: {
  params: { id: string }
}) {
  const { customer, brands, notes, communications, monthlyUsage } = await getCustomerDetail(params.id)

  if (!customer) notFound()

  const allComms = [...notes.map(n => ({ ...n, type: 'note' as const })),
    ...communications.map(c => ({ ...c, type: 'comm' as const }))]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

  return (
    <div className="p-6">
      {/* Geri */}
      <Link href="/musteriler" className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-700 mb-4">
        <ArrowLeft size={13} /> Müşteriler
      </Link>

      <div className="flex gap-5">
        {/* SOL KOLON */}
        <div className="flex-1 space-y-4">
          {/* Müşteri Bilgileri */}
          <div className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h1 className="text-lg font-bold text-gray-900">{customer.name ?? customer.email}</h1>
                <div className="text-sm text-gray-500">{customer.email}</div>
              </div>
              <div className="flex gap-2">
                <span className={cn('badge', PLAN_COLORS[customer.plan_id] ?? 'bg-gray-100 text-gray-600')}>
                  {PLAN_LABELS[customer.plan_id] ?? customer.plan_id}
                </span>
                <span className={cn('badge', STATUS_COLORS[customer.subscription_status] ?? 'bg-gray-100 text-gray-500')}>
                  {STATUS_LABELS[customer.subscription_status] ?? customer.subscription_status}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <InfoRow label="Kayıt Tarihi" value={formatDate(customer.created_at)} />
              <InfoRow label="Son Giriş" value={customer.last_login_at ? relativeTime(customer.last_login_at) : 'Hiç giriş yapmadı'} />
              {customer.current_period_end && (
                <InfoRow label="Abonelik Bitiş" value={formatDate(customer.current_period_end)} />
              )}
              {customer.trial_ends_at && (
                <InfoRow label="Deneme Bitiş" value={formatDate(customer.trial_ends_at)} />
              )}
              {customer.paddle_customer_id && (
                <div className="col-span-2">
                  <span className="text-gray-500">Paddle ID: </span>
                  <span className="font-medium text-gray-900">{customer.paddle_customer_id}</span>
                </div>
              )}
            </div>
          </div>

          {/* Markalar */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="px-5 py-3 border-b border-gray-50">
              <h2 className="text-sm font-semibold text-gray-700">
                Markalar ({brands.length})
              </h2>
            </div>
            {brands.length === 0 ? (
              <div className="px-5 py-6 text-center text-xs text-gray-400">Henüz marka yok</div>
            ) : (
              <div className="divide-y divide-gray-50">
                {brands.map((b) => (
                  <div key={b.id} className="px-5 py-3 flex items-center justify-between">
                    <div>
                      <div className="text-xs font-medium text-gray-900">{b.name}</div>
                      {b.sector && <div className="text-[11px] text-gray-400">{b.sector}</div>}
                    </div>
                    <div className="text-xs text-gray-500">{b.post_count} içerik</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Aylık Kullanım */}
          {monthlyUsage.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
              <div className="px-5 py-3 border-b border-gray-50">
                <h2 className="text-sm font-semibold text-gray-700">Aylık Kullanım (Son 3 Ay)</h2>
              </div>
              <table>
                <thead>
                  <tr>
                    <th>Ay</th>
                    <th>Üretilen</th>
                    <th>Yayınlanan</th>
                    <th>Yayın Oranı</th>
                  </tr>
                </thead>
                <tbody>
                  {monthlyUsage.map((m) => {
                    const rate = m.posts_generated > 0
                      ? Math.round((m.posts_published / m.posts_generated) * 100)
                      : 0
                    return (
                      <tr key={m.year_month}>
                        <td>{m.year_month}</td>
                        <td>{m.posts_generated}</td>
                        <td>{m.posts_published}</td>
                        <td>
                          <span className={cn(
                            'badge',
                            rate >= 70 ? 'bg-green-100 text-green-700' :
                            rate >= 40 ? 'bg-yellow-100 text-yellow-700' :
                            'bg-red-100 text-red-700'
                          )}>
                            %{rate}
                          </span>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}

          {/* İletişim Geçmişi */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="px-5 py-3 border-b border-gray-50">
              <h2 className="text-sm font-semibold text-gray-700">İletişim Geçmişi</h2>
            </div>
            <div className="divide-y divide-gray-50 max-h-60 overflow-y-auto">
              {allComms.length === 0 ? (
                <div className="px-5 py-6 text-center text-xs text-gray-400">
                  Henüz kayıt yok
                </div>
              ) : (
                allComms.map((item) => (
                  <div key={item.id} className="px-5 py-3">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        {item.type === 'note' ? (
                          <span className="badge bg-gray-100 text-gray-600">Not</span>
                        ) : (
                          <>
                            <span className="badge bg-blue-50 text-blue-600">
                              {(item as Communication).channel}
                            </span>
                            <span className="badge bg-gray-50 text-gray-500">
                              {(item as Communication).direction === 'inbound' ? 'Gelen' : 'Giden'}
                            </span>
                          </>
                        )}
                        <span className="text-[11px] text-gray-400">{item.created_by}</span>
                      </div>
                      <span className="text-[11px] text-gray-400">{relativeTime(item.created_at)}</span>
                    </div>
                    {item.type === 'comm' && (item as Communication).subject && (
                      <div className="text-xs font-medium text-gray-700 mb-0.5">
                        {(item as Communication).subject}
                      </div>
                    )}
                    <div className="text-xs text-gray-600">
                      {item.type === 'note' ? (item as Note).note : (item as Communication).note}
                    </div>
                  </div>
                ))
              )}
            </div>
            <div className="px-5 py-4 border-t border-gray-50 space-y-3">
              <AddNoteForm accountId={customer.id} />
              <AddCommunicationForm accountId={customer.id} />
            </div>
          </div>
        </div>

        {/* SAĞ KOLON */}
        <div className="w-64 space-y-4">
          {/* Hızlı Aksiyonlar */}
          <CustomerActions customer={{
            id: customer.id,
            email: customer.email,
            plan_id: customer.plan_id,
            paddle_customer_id: customer.paddle_customer_id,
          }} />

          {/* Etiketler */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-50">
              <h2 className="text-sm font-semibold text-gray-700">Etiketler</h2>
            </div>
            <div className="p-4">
              <TagManager
                accountId={customer.id}
                currentTags={customer.tags ?? []}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span className="text-gray-500">{label}: </span>
      <span className="font-medium text-gray-900">{value}</span>
    </div>
  )
}
