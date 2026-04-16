import { query } from '@/lib/db'
import { formatCurrency, PLAN_LABELS } from '@/lib/utils'
import { MonthSelector } from '@/components/reports/MonthSelector'

export const dynamic = 'force-dynamic'

async function getReportData(yearMonth: string) {
  const [year, month] = yearMonth.split('-').map(Number)
  const start = new Date(year, month - 1, 1)
  const end = new Date(year, month, 0, 23, 59, 59)
  const prevStart = new Date(year, month - 2, 1)
  const prevEnd = new Date(year, month - 1, 0, 23, 59, 59)

  const [
    newCustomers,
    prevNewCustomers,
    churnedCustomers,
    activeNow,
    mrrData,
    prevMrrData,
    planDist,
    postsGenerated,
    postsPublished,
    topByPosts,
    contentByType,
    contentByPlatform,
    trendUsage,
  ] = await Promise.all([
    query<{ count: string }>(`
      SELECT COUNT(*)::text as count FROM social.accounts
      WHERE created_at >= $1 AND created_at <= $2
    `, [start, end]),

    query<{ count: string }>(`
      SELECT COUNT(*)::text as count FROM social.accounts
      WHERE created_at >= $1 AND created_at <= $2
    `, [prevStart, prevEnd]),

    query<{ count: string }>(`
      SELECT COUNT(*)::text as count FROM social.subscriptions
      WHERE status = 'cancelled'
        AND updated_at >= $1 AND updated_at <= $2
    `, [start, end]),

    query<{ count: string }>(`
      SELECT COUNT(*)::text as count FROM social.subscriptions WHERE status = 'active'
    `),

    query<{ mrr: string }>(`
      SELECT COALESCE(SUM(pl.price_try), 0)::text as mrr
      FROM social.subscriptions s
      JOIN social.plan_limits pl ON pl.plan_id = s.plan_id
      WHERE s.status = 'active'
    `),

    query<{ mrr: string }>(`
      SELECT COALESCE(SUM(pl.price_try), 0)::text as mrr
      FROM social.subscriptions s
      JOIN social.plan_limits pl ON pl.plan_id = s.plan_id
      WHERE s.status = 'active'
        AND s.created_at <= $1
    `, [prevEnd]),

    query<{ plan_id: string; count: string }>(`
      SELECT plan_id, COUNT(*)::text as count
      FROM social.subscriptions WHERE status IN ('active','trialing')
      GROUP BY plan_id ORDER BY COUNT(*) DESC
    `),

    query<{ count: string }>(`
      SELECT COUNT(*)::text as count FROM social.posts
      WHERE created_at >= $1 AND created_at <= $2
    `, [start, end]),

    query<{ count: string }>(`
      SELECT COUNT(*)::text as count FROM social.posts
      WHERE status = 'published'
        AND created_at >= $1 AND created_at <= $2
    `, [start, end]),

    query<{ name: string | null; email: string; count: string }>(`
      SELECT a.name, a.email, COUNT(p.id)::text as count
      FROM social.posts p
      JOIN social.brands b ON b.id = p.brand_id
      JOIN social.workspaces w ON w.id = b.workspace_id
      JOIN social.accounts a ON a.id = w.account_id
      WHERE p.created_at >= $1 AND p.created_at <= $2
      GROUP BY a.id, a.name, a.email
      ORDER BY COUNT(p.id) DESC
      LIMIT 10
    `, [start, end]),

    query<{ content_type: string; count: string }>(`
      SELECT content_type, COUNT(*)::text as count FROM social.posts
      WHERE created_at >= $1 AND created_at <= $2 AND content_type IS NOT NULL
      GROUP BY content_type ORDER BY COUNT(*) DESC
    `, [start, end]),

    query<{ platform: string; count: string }>(`
      SELECT UNNEST(platforms) as platform, COUNT(*)::text as count
      FROM social.posts
      WHERE created_at >= $1 AND created_at <= $2
      GROUP BY UNNEST(platforms) ORDER BY COUNT(*) DESC LIMIT 5
    `, [start, end]),

    query<{ layer_b_count: string; layer_c_count: string; layer_b_cost: string; layer_c_cost: string }>(`
      SELECT
        COALESCE(SUM(layer_b_count), 0)::text as layer_b_count,
        COALESCE(SUM(layer_c_count), 0)::text as layer_c_count,
        COALESCE(SUM(layer_b_cost_usd), 0)::text as layer_b_cost,
        COALESCE(SUM(layer_c_cost_usd), 0)::text as layer_c_cost
      FROM social.trend_usage
      WHERE year_month = $1
    `, [yearMonth]),
  ])

  const nc = parseInt(newCustomers[0]?.count ?? '0')
  const pnc = parseInt(prevNewCustomers[0]?.count ?? '0')
  const cc = parseInt(churnedCustomers[0]?.count ?? '0')
  const ac = parseInt(activeNow[0]?.count ?? '0')
  const mrr = parseInt(mrrData[0]?.mrr ?? '0')
  const prevMrr = parseInt(prevMrrData[0]?.mrr ?? '0')
  const pg = parseInt(postsGenerated[0]?.count ?? '0')
  const pp = parseInt(postsPublished[0]?.count ?? '0')
  const publishRate = pg > 0 ? Math.round((pp / pg) * 100) : 0
  const arpu = ac > 0 ? Math.round(mrr / ac) : 0
  const churnRate = ac > 0 ? ((cc / ac) * 100).toFixed(1) : '0.0'
  const mrrGrowth = prevMrr > 0 ? Math.round(((mrr - prevMrr) / prevMrr) * 100) : 0

  const tLayerB = parseInt(trendUsage[0]?.layer_b_count ?? '0')
  const tLayerC = parseInt(trendUsage[0]?.layer_c_count ?? '0')
  const tCostB = parseFloat(trendUsage[0]?.layer_b_cost ?? '0')
  const tCostC = parseFloat(trendUsage[0]?.layer_c_cost ?? '0')

  return {
    nc, pnc, cc, ac, mrr, prevMrr, mrrGrowth, pg, pp, publishRate, arpu, churnRate,
    planDist, topByPosts, contentByType, contentByPlatform,
    tLayerB, tLayerC, tCostB, tCostC,
  }
}

function getMonthOptions() {
  const options = []
  const now = new Date()
  for (let i = 0; i < 12; i++) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    const value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    const label = d.toLocaleDateString('tr-TR', { year: 'numeric', month: 'long' })
    options.push({ value, label })
  }
  return options
}

export default async function RaporlarPage({
  searchParams,
}: {
  searchParams: { month?: string }
}) {
  const now = new Date()
  const defaultMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  const selectedMonth = searchParams.month ?? defaultMonth
  const monthOptions = getMonthOptions()
  const selectedLabel = monthOptions.find(m => m.value === selectedMonth)?.label ?? selectedMonth

  const data = await getReportData(selectedMonth)

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">Raporlar — {selectedLabel}</h1>
        <MonthSelector options={monthOptions} selected={selectedMonth} />
      </div>

      {/* Büyüme Metrikleri */}
      <ReportSection title="📈 Büyüme Metrikleri">
        <div className="grid grid-cols-3 gap-3">
          <MetricCard
            label="Yeni Müşteri"
            value={data.nc}
            sub={data.pnc > 0 ? `Geçen ay: ${data.pnc}` : undefined}
          />
          <MetricCard label="Churn" value={data.cc} sub={`Churn rate: %${data.churnRate}`} />
          <MetricCard label="Net Büyüme" value={data.nc - data.cc} />
          <MetricCard label="MRR" value={formatCurrency(data.mrr)} sub={
            data.mrrGrowth !== 0
              ? `${data.mrrGrowth > 0 ? '+' : ''}%${data.mrrGrowth} geçen aya göre`
              : undefined
          } />
          <MetricCard label="Toplam Aktif" value={data.ac} />
          <MetricCard label="ARPU" value={formatCurrency(data.arpu)} />
        </div>
      </ReportSection>

      {/* Ürün Kullanımı */}
      <ReportSection title="📊 Ürün Kullanımı">
        <div className="grid grid-cols-2 gap-5">
          <div>
            <div className="grid grid-cols-2 gap-3 mb-4">
              <MetricCard label="Üretilen İçerik" value={data.pg} />
              <MetricCard label="Yayınlanan" value={data.pp} />
              <MetricCard label="Yayın Oranı" value={`%${data.publishRate}`} />
            </div>
          </div>
          <div className="space-y-2">
            <div className="text-xs font-semibold text-gray-600 mb-2">İçerik Tipi</div>
            {data.contentByType.map((c) => (
              <div key={c.content_type} className="flex items-center justify-between text-xs">
                <span className="text-gray-600">{c.content_type}</span>
                <span className="font-medium">{c.count}</span>
              </div>
            ))}
            <div className="text-xs font-semibold text-gray-600 mt-3 mb-2">Platform</div>
            {data.contentByPlatform.map((c) => (
              <div key={c.platform} className="flex items-center justify-between text-xs">
                <span className="text-gray-600">{c.platform}</span>
                <span className="font-medium">{c.count}</span>
              </div>
            ))}
          </div>
        </div>
      </ReportSection>

      {/* Trend Kullanımı & Maliyet */}
      <ReportSection title="🔍 Trend Kullanımı & Maliyet">
        <div className="grid grid-cols-4 gap-3">
          <MetricCard label="Layer B Tetik" value={data.tLayerB} sub="Kişisel arama" />
          <MetricCard label="Layer C Rapor" value={data.tLayerC} sub="Aylık PDF" />
          <MetricCard label="Layer B Maliyet" value={`$${data.tCostB.toFixed(2)}`} sub="Serper + Haiku" />
          <MetricCard label="Layer C Maliyet" value={`$${data.tCostC.toFixed(2)}`} sub="Apify + Claude" />
        </div>
        <div className="mt-3 text-xs text-gray-400">
          Toplam trend maliyeti: ${(data.tCostB + data.tCostC).toFixed(2)}
        </div>
      </ReportSection>

      {/* Plan Dağılımı */}
      <ReportSection title="🎯 Plan Dağılımı (Anlık)">
        <div className="grid grid-cols-5 gap-3">
          {data.planDist.map((p) => (
            <div key={p.plan_id} className="text-center bg-gray-50 rounded-lg p-3">
              <div className="text-lg font-bold text-gray-900">{p.count}</div>
              <div className="text-xs text-gray-500 mt-0.5">{PLAN_LABELS[p.plan_id] ?? p.plan_id}</div>
            </div>
          ))}
        </div>
      </ReportSection>

      {/* En Aktif Müşteriler */}
      <ReportSection title="🏆 En Aktif Müşteriler (Bu Ay)">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Müşteri</th>
              <th>Üretilen İçerik</th>
            </tr>
          </thead>
          <tbody>
            {data.topByPosts.length === 0 ? (
              <tr>
                <td colSpan={3} className="text-center text-gray-400 py-6 text-xs">Bu ay içerik üretilmedi</td>
              </tr>
            ) : (
              data.topByPosts.map((c, i) => (
                <tr key={c.email}>
                  <td className="text-gray-400 text-xs">{i + 1}</td>
                  <td>
                    <div className="text-xs font-medium text-gray-900">{c.name ?? c.email}</div>
                    <div className="text-[11px] text-gray-400">{c.email}</div>
                  </td>
                  <td className="font-semibold text-sm">{c.count}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </ReportSection>
    </div>
  )
}

function ReportSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
      <div className="px-5 py-3 border-b border-gray-50">
        <h2 className="text-sm font-semibold text-gray-700">{title}</h2>
      </div>
      <div className="p-5">{children}</div>
    </div>
  )
}

function MetricCard({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div className="bg-gray-50 rounded-lg p-3">
      <div className="text-[11px] text-gray-500 mb-1">{label}</div>
      <div className="text-lg font-bold text-gray-900">{value}</div>
      {sub && <div className="text-[11px] text-gray-400 mt-0.5">{sub}</div>}
    </div>
  )
}
