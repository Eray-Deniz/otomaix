import { query } from '@/lib/db'
import { formatCurrency, PLAN_COLORS, PLAN_LABELS, relativeTime, formatDate } from '@/lib/utils'
import { PlanDistributionChart } from '@/components/charts/PlanDistributionChart'
import { ContentBarChart } from '@/components/charts/ContentBarChart'
import { Users, TrendingUp, DollarSign, UserMinus, ExternalLink } from 'lucide-react'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

async function getDashboardData() {
  const now = new Date()
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1)
  const lastMonthStart = new Date(now.getFullYear(), now.getMonth() - 1, 1)

  const [
    activeCustomers,
    newThisMonth,
    newLastMonth,
    mrrData,
    churnThisMonth,
    planDistribution,
    contentLast30,
    recentCustomers,
    churnRisk,
    paymentIssues,
  ] = await Promise.all([
    // Aktif müşteri sayısı
    query<{ count: string }>(`
      SELECT COUNT(DISTINCT a.id)::text as count
      FROM social.accounts a
      JOIN social.subscriptions s ON s.account_id = a.id
      WHERE s.status IN ('active', 'trialing')
    `),

    // Bu ay yeni müşteri
    query<{ count: string }>(`
      SELECT COUNT(*)::text as count FROM social.accounts
      WHERE created_at >= $1
    `, [monthStart]),

    // Geçen ay yeni müşteri
    query<{ count: string }>(`
      SELECT COUNT(*)::text as count FROM social.accounts
      WHERE created_at >= $1 AND created_at < $2
    `, [lastMonthStart, monthStart]),

    // MRR
    query<{ mrr: string }>(`
      SELECT COALESCE(SUM(pl.price_try), 0)::text as mrr
      FROM social.subscriptions s
      JOIN social.plan_limits pl ON pl.plan_id = s.plan_id
      WHERE s.status = 'active'
    `),

    // Bu ay churn
    query<{ count: string }>(`
      SELECT COUNT(*)::text as count FROM social.subscriptions
      WHERE status = 'cancelled'
        AND updated_at >= $1
    `, [monthStart]),

    // Plan dağılımı
    query<{ plan_id: string; count: string }>(`
      SELECT s.plan_id, COUNT(*)::text as count
      FROM social.subscriptions s
      WHERE s.status IN ('active', 'trialing')
      GROUP BY s.plan_id
      ORDER BY COUNT(*) DESC
    `),

    // Son 30 gün içerik üretimi (günlük)
    query<{ day: string; count: string }>(`
      SELECT DATE(created_at) as day, COUNT(*)::text as count
      FROM social.posts
      WHERE created_at >= NOW() - INTERVAL '30 days'
      GROUP BY DATE(created_at)
      ORDER BY day ASC
    `),

    // Son kayıt olanlar
    query<{
      id: string; email: string; name: string; plan_id: string;
      created_at: string; subscription_status: string;
    }>(`
      SELECT a.id, a.email, a.name, a.plan_id, a.created_at,
             COALESCE(s.status, 'none') as subscription_status
      FROM social.accounts a
      LEFT JOIN social.subscriptions s ON s.account_id = a.id
      ORDER BY a.created_at DESC
      LIMIT 10
    `),

    // Churn riski (14+ gün giriş yapmamış)
    query<{ id: string; email: string; name: string; plan_id: string; last_login_at: string }>(`
      SELECT a.id, a.email, a.name, a.plan_id, a.last_login_at
      FROM social.accounts a
      LEFT JOIN social.subscriptions s ON s.account_id = a.id
      WHERE (a.last_login_at IS NULL OR a.last_login_at < NOW() - INTERVAL '14 days')
        AND s.status = 'active'
        AND NOT EXISTS (
          SELECT 1 FROM crm.account_tags t
          WHERE t.account_id = a.id AND t.tag = 'Churn Riski'
        )
      ORDER BY a.last_login_at ASC NULLS FIRST
      LIMIT 10
    `),

    // Ödeme sorunları
    query<{ id: string; email: string; name: string; plan_id: string; updated_at: string }>(`
      SELECT a.id, a.email, a.name, a.plan_id, s.updated_at
      FROM social.accounts a
      JOIN social.subscriptions s ON s.account_id = a.id
      WHERE s.status = 'past_due'
      ORDER BY s.updated_at ASC
      LIMIT 10
    `),
  ])

  const activeCount = parseInt(activeCustomers[0]?.count ?? '0')
  const newCount = parseInt(newThisMonth[0]?.count ?? '0')
  const lastMonthCount = parseInt(newLastMonth[0]?.count ?? '0')
  const growthPct = lastMonthCount > 0 ? Math.round(((newCount - lastMonthCount) / lastMonthCount) * 100) : 0
  const mrr = parseInt(mrrData[0]?.mrr ?? '0')
  const churn = parseInt(churnThisMonth[0]?.count ?? '0')

  return {
    activeCount,
    newCount,
    growthPct,
    mrr,
    churn,
    planDistribution,
    contentLast30,
    recentCustomers,
    churnRisk,
    paymentIssues,
  }
}

export default async function DashboardPage() {
  const data = await getDashboardData()

  const metrics = [
    {
      label: 'Toplam Aktif Müşteri',
      value: data.activeCount.toLocaleString('tr-TR'),
      icon: Users,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
    },
    {
      label: 'Bu Ay Yeni Müşteri',
      value: data.newCount.toString(),
      sub: data.growthPct !== 0
        ? `${data.growthPct > 0 ? '+' : ''}${data.growthPct}% geçen aya göre`
        : 'Geçen ayla aynı',
      subColor: data.growthPct >= 0 ? 'text-green-600' : 'text-red-600',
      icon: TrendingUp,
      color: 'text-green-600',
      bg: 'bg-green-50',
    },
    {
      label: 'Aylık Gelir (MRR)',
      value: formatCurrency(data.mrr),
      icon: DollarSign,
      color: 'text-purple-600',
      bg: 'bg-purple-50',
    },
    {
      label: 'Churn Bu Ay',
      value: data.churn.toString(),
      icon: UserMinus,
      color: 'text-red-600',
      bg: 'bg-red-50',
    },
  ]

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">Genel Bakış</h1>
        <span className="text-xs text-gray-400">
          Son güncelleme: {formatDate(new Date(), 'dd.MM.yyyy HH:mm')}
        </span>
      </div>

      {/* Metrik Kartları */}
      <div className="grid grid-cols-4 gap-4">
        {metrics.map((m) => (
          <div key={m.label} className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs text-gray-500 font-medium">{m.label}</span>
              <div className={`w-8 h-8 rounded-lg ${m.bg} flex items-center justify-center`}>
                <m.icon size={15} className={m.color} />
              </div>
            </div>
            <div className="text-2xl font-bold text-gray-900">{m.value}</div>
            {m.sub && (
              <div className={`text-xs mt-1 ${m.subColor ?? 'text-gray-400'}`}>{m.sub}</div>
            )}
          </div>
        ))}
      </div>

      {/* Grafikler */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Plan Dağılımı</h2>
          <PlanDistributionChart
            data={data.planDistribution.map(d => ({
              name: PLAN_LABELS[d.plan_id] ?? d.plan_id,
              value: parseInt(d.count),
              plan: d.plan_id,
            }))}
          />
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">
            Son 30 Gün — Üretilen İçerik
          </h2>
          <ContentBarChart
            data={data.contentLast30.map(d => ({
              day: d.day,
              count: parseInt(d.count),
            }))}
          />
        </div>
      </div>

      {/* Tablolar */}
      <div className="grid grid-cols-3 gap-4">
        {/* Son Kayıt Olanlar */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-50 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-gray-700">Son Kayıt Olanlar</h2>
            <Link href="/musteriler" className="text-xs text-blue-600 hover:underline flex items-center gap-1">
              Tümü <ExternalLink size={10} />
            </Link>
          </div>
          <div className="divide-y divide-gray-50">
            {data.recentCustomers.length === 0 ? (
              <div className="px-4 py-8 text-center text-gray-400 text-xs">Henüz müşteri yok</div>
            ) : (
              data.recentCustomers.map((c) => (
                <Link
                  key={c.id}
                  href={`/musteriler/${c.id}`}
                  className="block px-4 py-2.5 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="min-w-0">
                      <div className="text-xs font-medium text-gray-900 truncate">
                        {c.name ?? c.email}
                      </div>
                      <div className="text-[11px] text-gray-400 truncate">{c.email}</div>
                    </div>
                    <span className={`badge flex-shrink-0 ml-2 ${PLAN_COLORS[c.plan_id] ?? 'bg-gray-100 text-gray-600'}`}>
                      {PLAN_LABELS[c.plan_id] ?? c.plan_id}
                    </span>
                  </div>
                  <div className="text-[11px] text-gray-400 mt-0.5">
                    {relativeTime(c.created_at)}
                  </div>
                </Link>
              ))
            )}
          </div>
        </div>

        {/* Churn Riski */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-50">
            <h2 className="text-sm font-semibold text-gray-700">
              Churn Riski
              {data.churnRisk.length > 0 && (
                <span className="ml-2 badge bg-orange-100 text-orange-700">
                  {data.churnRisk.length}
                </span>
              )}
            </h2>
          </div>
          <div className="divide-y divide-gray-50">
            {data.churnRisk.length === 0 ? (
              <div className="px-4 py-8 text-center text-gray-400 text-xs">Churn riski yok</div>
            ) : (
              data.churnRisk.map((c) => (
                <Link
                  key={c.id}
                  href={`/musteriler/${c.id}`}
                  className="block px-4 py-2.5 hover:bg-gray-50 transition-colors"
                >
                  <div className="text-xs font-medium text-gray-900 truncate">
                    {c.name ?? c.email}
                  </div>
                  <div className="text-[11px] text-red-500 mt-0.5">
                    {c.last_login_at ? `Son giriş: ${relativeTime(c.last_login_at)}` : 'Hiç giriş yapmadı'}
                  </div>
                </Link>
              ))
            )}
          </div>
        </div>

        {/* Ödeme Sorunları */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-50">
            <h2 className="text-sm font-semibold text-gray-700">
              Ödeme Sorunları
              {data.paymentIssues.length > 0 && (
                <span className="ml-2 badge bg-red-100 text-red-700">
                  {data.paymentIssues.length}
                </span>
              )}
            </h2>
          </div>
          <div className="divide-y divide-gray-50">
            {data.paymentIssues.length === 0 ? (
              <div className="px-4 py-8 text-center text-gray-400 text-xs">Ödeme sorunu yok</div>
            ) : (
              data.paymentIssues.map((c) => (
                <Link
                  key={c.id}
                  href={`/musteriler/${c.id}`}
                  className="block px-4 py-2.5 hover:bg-gray-50 transition-colors"
                >
                  <div className="text-xs font-medium text-gray-900 truncate">
                    {c.name ?? c.email}
                  </div>
                  <div className="text-[11px] text-gray-400 mt-0.5">
                    {PLAN_LABELS[c.plan_id] ?? c.plan_id} —{' '}
                    <span className="text-red-500">
                      {relativeTime(c.updated_at)}
                    </span>
                  </div>
                </Link>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
