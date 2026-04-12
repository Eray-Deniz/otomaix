import { query } from '@/lib/db'
import { relativeTime, PLAN_LABELS } from '@/lib/utils'
import { MarkChurnRisk } from '@/components/operations/MarkChurnRisk'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

async function getOperationData() {
  const [failedPosts, paymentIssues, failedGenerations, churnCandidates] = await Promise.all([
    // Başarısız yayınlar (son 7 gün)
    query<{
      post_id: string
      brand_name: string
      platforms: string[]
      created_at: string
      status: string
    }>(`
      SELECT p.id as post_id, b.name as brand_name, p.platforms, p.created_at, p.status
      FROM social.posts p
      JOIN social.brands b ON b.id = p.brand_id
      WHERE p.status = 'failed'
        AND p.created_at > NOW() - INTERVAL '7 days'
      ORDER BY p.created_at DESC
      LIMIT 50
    `),

    // Ödeme sorunları
    query<{
      account_id: string
      email: string
      name: string | null
      plan_id: string
      updated_at: string
    }>(`
      SELECT a.id as account_id, a.email, a.name, a.plan_id, s.updated_at
      FROM social.accounts a
      JOIN social.subscriptions s ON s.account_id = a.id
      WHERE s.status = 'past_due'
      ORDER BY s.updated_at ASC
    `),

    // fal.ai üretim hataları (son 24 saat, failed + fal_job_id var)
    query<{
      post_id: string
      brand_name: string
      content_type: string
      fal_job_id: string
      created_at: string
    }>(`
      SELECT p.id as post_id, b.name as brand_name, p.content_type, p.fal_job_id, p.created_at
      FROM social.posts p
      JOIN social.brands b ON b.id = p.brand_id
      WHERE p.status = 'failed'
        AND p.fal_job_id IS NOT NULL
        AND p.created_at > NOW() - INTERVAL '24 hours'
      ORDER BY p.created_at DESC
      LIMIT 20
    `),

    // Churn riski adayları (14+ gün giriş yok, aktif üyelik, etiket yok)
    query<{
      id: string
      email: string
      name: string | null
      plan_id: string
      last_login_at: string | null
    }>(`
      SELECT a.id, a.email, a.name, a.plan_id, a.last_login_at
      FROM social.accounts a
      JOIN social.subscriptions s ON s.account_id = a.id
      WHERE s.status = 'active'
        AND (a.last_login_at IS NULL OR a.last_login_at < NOW() - INTERVAL '14 days')
        AND NOT EXISTS (
          SELECT 1 FROM crm.account_tags t
          WHERE t.account_id = a.id AND t.tag = 'Churn Riski'
        )
      ORDER BY a.last_login_at ASC NULLS FIRST
      LIMIT 20
    `),
  ])

  return { failedPosts, paymentIssues, failedGenerations, churnCandidates }
}

export default async function OperasyonPage() {
  const { failedPosts, paymentIssues, failedGenerations, churnCandidates } = await getOperationData()

  const totalIssues = failedPosts.length + paymentIssues.length + churnCandidates.length

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center gap-3">
        <h1 className="text-xl font-bold text-gray-900">Operasyon</h1>
        {totalIssues > 0 && (
          <span className="badge bg-red-100 text-red-700 text-xs px-2 py-0.5">
            {totalIssues} sorun
          </span>
        )}
      </div>

      {/* Yayın Hataları */}
      <Section
        title="Yayın Hataları"
        count={failedPosts.length}
        icon="📤"
        emptyText="Son 7 günde yayın hatası yok"
      >
        <table>
          <thead>
            <tr>
              <th>Marka</th>
              <th>Platform</th>
              <th>Hata Zamanı</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {failedPosts.map((p) => (
              <tr key={p.post_id}>
                <td className="font-medium text-xs">{p.brand_name}</td>
                <td className="text-xs text-gray-500">
                  {(p.platforms ?? []).join(', ')}
                </td>
                <td className="text-xs text-gray-500">{relativeTime(p.created_at)}</td>
                <td>
                  <form action={`${process.env.NEXT_PUBLIC_API_URL}/posts/${p.post_id}/regenerate`} method="POST">
                    <button
                      type="submit"
                      className="flex items-center gap-1 text-xs text-blue-600 hover:underline"
                    >
                      <RefreshCw size={11} /> Yeniden Dene
                    </button>
                  </form>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Section>

      {/* Ödeme Sorunları */}
      <Section
        title="Ödeme Sorunları"
        count={paymentIssues.length}
        icon="💳"
        emptyText="Aktif ödeme sorunu yok"
      >
        <table>
          <thead>
            <tr>
              <th>Müşteri</th>
              <th>Plan</th>
              <th>Ödeme Tarihi</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {paymentIssues.map((p) => (
              <tr key={p.account_id}>
                <td>
                  <div className="text-xs font-medium text-gray-900">{p.name ?? p.email}</div>
                  <div className="text-[11px] text-gray-400">{p.email}</div>
                </td>
                <td className="text-xs">{PLAN_LABELS[p.plan_id] ?? p.plan_id}</td>
                <td className="text-xs text-red-500">{relativeTime(p.updated_at)}</td>
                <td>
                  <Link
                    href={`/musteriler/${p.account_id}`}
                    className="text-xs text-blue-600 hover:underline"
                  >
                    Müşteriye Git
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Section>

      {/* fal.ai Üretim Hataları */}
      <Section
        title="fal.ai Üretim Hataları (24 saat)"
        count={failedGenerations.length}
        icon="🤖"
        emptyText="Son 24 saatte üretim hatası yok"
      >
        <table>
          <thead>
            <tr>
              <th>Marka</th>
              <th>İçerik Tipi</th>
              <th>Job ID</th>
              <th>Zaman</th>
            </tr>
          </thead>
          <tbody>
            {failedGenerations.map((g) => (
              <tr key={g.post_id}>
                <td className="text-xs font-medium">{g.brand_name}</td>
                <td className="text-xs text-gray-500">{g.content_type}</td>
                <td className="text-[11px] text-gray-400 font-mono">{g.fal_job_id?.slice(0, 16)}...</td>
                <td className="text-xs text-gray-500">{relativeTime(g.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Section>

      {/* Churn Riski */}
      <Section
        title="Churn Riski — Etiketlenmemiş (14+ gün giriş yok)"
        count={churnCandidates.length}
        icon="⚠️"
        emptyText="Yeni churn riski adayı yok"
      >
        <table>
          <thead>
            <tr>
              <th>Müşteri</th>
              <th>Plan</th>
              <th>Son Giriş</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {churnCandidates.map((c) => (
              <tr key={c.id}>
                <td>
                  <div className="text-xs font-medium text-gray-900">{c.name ?? c.email}</div>
                  <div className="text-[11px] text-gray-400">{c.email}</div>
                </td>
                <td className="text-xs">{PLAN_LABELS[c.plan_id] ?? c.plan_id}</td>
                <td className="text-xs text-red-500">
                  {c.last_login_at ? relativeTime(c.last_login_at) : 'Hiç giriş yapmadı'}
                </td>
                <td>
                  <div className="flex items-center gap-2">
                    <MarkChurnRisk accountId={c.id} />
                    <Link
                      href={`/musteriler/${c.id}`}
                      className="text-xs text-blue-600 hover:underline"
                    >
                      Detay
                    </Link>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Section>
    </div>
  )
}

function Section({
  title,
  count,
  icon,
  emptyText,
  children,
}: {
  title: string
  count: number
  icon: string
  emptyText: string
  children: React.ReactNode
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
      <div className="px-5 py-3 border-b border-gray-50 flex items-center gap-2">
        <span>{icon}</span>
        <h2 className="text-sm font-semibold text-gray-700">{title}</h2>
        {count > 0 && (
          <span className="badge bg-red-100 text-red-700">{count}</span>
        )}
      </div>
      {count === 0 ? (
        <div className="px-5 py-8 text-center text-xs text-gray-400 flex items-center justify-center gap-2">
          <AlertTriangle size={14} className="text-green-400" />
          {emptyText}
        </div>
      ) : (
        children
      )}
    </div>
  )
}
