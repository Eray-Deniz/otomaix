import { query } from '@/lib/db'
import {
  cn,
  PLAN_COLORS,
  PLAN_LABELS,
  STATUS_COLORS,
  STATUS_LABELS,
  relativeTime,
} from '@/lib/utils'
import Link from 'next/link'
import { CustomerFilters } from '@/components/customers/CustomerFilters'
import { Download } from 'lucide-react'

export const dynamic = 'force-dynamic'

interface Customer {
  id: string
  email: string
  name: string | null
  plan_id: string
  created_at: string
  last_login_at: string | null
  subscription_status: string
  brand_count: string
  tags: string[] | null
  total_posts_generated: string
}

interface SearchParams {
  plan?: string
  status?: string
  tag?: string
  login?: string
  q?: string
  page?: string
}

async function getCustomers(params: SearchParams): Promise<{ customers: Customer[]; total: number }> {
  const page = parseInt(params.page ?? '1')
  const perPage = 25
  const offset = (page - 1) * perPage

  const conditions: string[] = ['1=1']
  const values: unknown[] = []
  let paramIdx = 1

  if (params.plan && params.plan !== 'all') {
    conditions.push(`co.plan_id = $${paramIdx++}`)
    values.push(params.plan)
  }

  if (params.status && params.status !== 'all') {
    conditions.push(`co.subscription_status = $${paramIdx++}`)
    values.push(params.status)
  }

  if (params.tag && params.tag !== 'all') {
    conditions.push(`$${paramIdx++} = ANY(co.tags)`)
    values.push(params.tag)
  }

  if (params.login && params.login !== 'all') {
    if (params.login === '7') {
      conditions.push(`co.last_login_at >= NOW() - INTERVAL '7 days'`)
    } else if (params.login === '30') {
      conditions.push(`co.last_login_at >= NOW() - INTERVAL '30 days' AND co.last_login_at < NOW() - INTERVAL '7 days'`)
    } else if (params.login === '30plus') {
      conditions.push(`(co.last_login_at IS NULL OR co.last_login_at < NOW() - INTERVAL '30 days')`)
    }
  }

  if (params.q) {
    conditions.push(`(co.email ILIKE $${paramIdx} OR co.name ILIKE $${paramIdx})`)
    values.push(`%${params.q}%`)
    paramIdx++
  }

  const where = conditions.join(' AND ')

  const [countResult, rows] = await Promise.all([
    query<{ count: string }>(
      `SELECT COUNT(*)::text as count FROM crm.customer_overview co WHERE ${where}`,
      values
    ),
    query<Customer>(
      `SELECT co.id, co.email, co.name, co.plan_id, co.created_at, co.last_login_at,
              co.subscription_status, co.brand_count::text, co.tags,
              co.total_posts_generated::text
       FROM crm.customer_overview co WHERE ${where}
       ORDER BY co.created_at DESC
       LIMIT ${perPage} OFFSET ${offset}`,
      values
    ),
  ])

  return {
    customers: rows,
    total: parseInt(countResult[0]?.count ?? '0'),
  }
}

export default async function MusterilerPage({
  searchParams,
}: {
  searchParams: SearchParams
}) {
  const { customers, total } = await getCustomers(searchParams)
  const page = parseInt(searchParams.page ?? '1')
  const totalPages = Math.ceil(total / 25)

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Müşteriler</h1>
          <p className="text-xs text-gray-500 mt-0.5">{total} müşteri</p>
        </div>
        <a
          href={`/api/customers/export?${new URLSearchParams(searchParams as Record<string, string>).toString()}`}
          className="flex items-center gap-1.5 text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg transition-colors"
        >
          <Download size={13} />
          CSV İndir
        </a>
      </div>

      {/* Filtreler — client component */}
      <CustomerFilters initialValues={searchParams} />

      {/* Tablo */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table>
            <thead>
              <tr>
                <th>Ad / Email</th>
                <th>Plan</th>
                <th>Marka</th>
                <th>Toplam İçerik</th>
                <th>Son Giriş</th>
                <th>Etiketler</th>
                <th>Durum</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {customers.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center text-gray-400 py-12">
                    Müşteri bulunamadı
                  </td>
                </tr>
              ) : (
                customers.map((c) => {
                  const daysSinceLogin = c.last_login_at
                    ? Math.floor((Date.now() - new Date(c.last_login_at).getTime()) / 86400000)
                    : null
                  const loginOld = daysSinceLogin === null || daysSinceLogin > 14

                  return (
                    <tr key={c.id}>
                      <td>
                        <div className="font-medium text-gray-900 text-xs">{c.name ?? '—'}</div>
                        <div className="text-gray-400 text-[11px]">{c.email}</div>
                      </td>
                      <td>
                        <span className={cn('badge', PLAN_COLORS[c.plan_id] ?? 'bg-gray-100 text-gray-600')}>
                          {PLAN_LABELS[c.plan_id] ?? c.plan_id}
                        </span>
                      </td>
                      <td className="text-gray-600">{c.brand_count}</td>
                      <td className="text-gray-600">{c.total_posts_generated}</td>
                      <td>
                        <span className={cn('text-xs', loginOld ? 'text-red-500' : 'text-gray-500')}>
                          {c.last_login_at ? relativeTime(c.last_login_at) : 'Hiç giriş yapmadı'}
                        </span>
                      </td>
                      <td>
                        <div className="flex flex-wrap gap-1">
                          {(c.tags ?? []).map((tag) => (
                            <span key={tag} className="badge bg-gray-100 text-gray-600">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td>
                        <span className={cn('badge', STATUS_COLORS[c.subscription_status] ?? 'bg-gray-100 text-gray-500')}>
                          {STATUS_LABELS[c.subscription_status] ?? c.subscription_status}
                        </span>
                      </td>
                      <td>
                        <Link
                          href={`/musteriler/${c.id}`}
                          className="text-xs text-blue-600 hover:underline whitespace-nowrap"
                        >
                          Görüntüle
                        </Link>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Sayfalama */}
        {totalPages > 1 && (
          <div className="px-4 py-3 border-t border-gray-50 flex items-center justify-between">
            <span className="text-xs text-gray-500">
              Sayfa {page} / {totalPages} ({total} müşteri)
            </span>
            <div className="flex gap-2">
              {page > 1 && (
                <Link
                  href={`/musteriler?${new URLSearchParams({ ...searchParams, page: String(page - 1) }).toString()}`}
                  className="text-xs px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  ← Önceki
                </Link>
              )}
              {page < totalPages && (
                <Link
                  href={`/musteriler?${new URLSearchParams({ ...searchParams, page: String(page + 1) }).toString()}`}
                  className="text-xs px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  Sonraki →
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
