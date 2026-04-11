'use client'

import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts'

const PIE_COLORS = ['#6366f1', '#8b5cf6', '#a78bfa']

interface ChartEntry {
  name: string
  value: number
}

export function CompetitorChart({ data }: { data: ChartEntry[] }) {
  if (data.length === 0) return null
  return (
    <div>
      <p className="text-xs text-gray-500 mb-2">İçerik Dağılımı</p>
      <ResponsiveContainer width="100%" height={160}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            outerRadius={60}
            dataKey="value"
            label={({ name, percent }) => `${name} ${Math.round((percent ?? 0) * 100)}%`}
            labelLine={false}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
